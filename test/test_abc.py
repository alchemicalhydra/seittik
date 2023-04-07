from seittik.utils.abc import NonStrSequence


def test_nonstrsequence_subclass_notimplemented():
    class NonStringSequenceSubclass(NonStrSequence):
        pass
    assert NonStringSequenceSubclass.__subclasshook__(int) is NotImplemented
